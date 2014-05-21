package com.coral.workers

import scala.collection.mutable.ListBuffer
import scala.concurrent.Await
import scala.concurrent.duration._
import akka.actor._
import akka.pattern.ask
import akka.util.Timeout
import com.coral.messages._
import com.lionfish.client._

class DatabaseWorker extends Actor {
  private val sessionWorkerSystemPort = 7780
  private implicit val timeout = Timeout(20 seconds)

  // Session worker system
  private val sessionWorkerPath =
    s"akka.tcp://sessionWorkerSystem@localhost:$sessionWorkerSystemPort/user/sessionWorker"
  private val sessionWorker = context.actorSelection(sessionWorkerPath)

  Database.setServerAddress("127.0.0.1")
  Database.setServerPort(7777)
  private val seqStream = Database.getSequenceStream
  private val batchStream = Database.getBatchStream

  private def handshake(): Map[String, Any] = {
    var result: Map[String, Any] = null

    try {
      val future = sessionWorker ? Handshake()
      val clientUuid = Await.result[Any](future, timeout.duration)
        .asInstanceOf[String]

      result = Map(
        "status" -> true,
        "client_id" -> clientUuid
      )
    } catch {
      case e: Exception => {
        println(s"Failed to process handshake. Error message: $e")
        result = Map("status" -> false)
      }
    }

    result
  }

  private def signIn(clientUuid: String,
                     username: String,
                     password: String): Map[String, Any] = {
    var result: Map[String, Any] = null

    try {
      seqStream << Database.getByUsername(username)
      val userList = seqStream.execute()
        .asInstanceOf[List[Map[String, Any]]]

      // Checks if given username exists
      if (userList.length == 1 && userList(0).contains("uuid")) {
        // TODO: Authentication
        val userUuid = userList(0)("uuid").asInstanceOf[String]

        val future = sessionWorker ? SignIn(clientUuid, userUuid)
        val status = Await.result[Any](future, timeout.duration)
          .asInstanceOf[Boolean]

        result = Map("status" -> status)
      } else {
        throw new Exception("Unknown username.")
      }
    } catch {
      case e: Exception => {
        println(s"Failed to process signIn. Error message: $e")
        result = Map("status" -> false)
      }
    }

    result
  }

  private def signOut(clientUuid: String): Map[String, Any] = {
    var result: Map[String, Any] = null

    try {
      val future = sessionWorker ? SignOut(clientUuid)
      val status = Await.result[Any](future, timeout.duration)
        .asInstanceOf[Boolean]

      result = Map("status" -> status)
    } catch {
      case e: Exception => {
        println(s"Failed to process signOut. Error message: $e")
        result = Map("status" -> false)
      }
    }

    result
  }

  private def getFeedList(clientUuid: String): Map[String, Any] = {
    var result: Map[String, Any] = null

    try {
      // Gets userUuid from session
      val future = sessionWorker ? SessionDetails(clientUuid)
      val userUuid = Await.result[Any](future, timeout.duration)
        .asInstanceOf[String]

      // Checks if user is signed in
      if (userUuid.length > 0) {
        val rawResult: ListBuffer[Map[String, Any]] = ListBuffer()

        // Fetches feed nodes
        seqStream << Database.getUserFeeds(userUuid)
        val feedNodeList = seqStream.execute()
          .asInstanceOf[List[List[Map[String, Any]]]](0)

        // Fetches included tag nodes of each feed
        val includesRelType = "<<INCLUDES>>"
        for (item <- feedNodeList) {
          val uuid = item("uuid").asInstanceOf[String]
          batchStream << Database.getChildren(uuid, includesRelType)
        }
        val includedTagNodeList = batchStream.execute()
          .asInstanceOf[List[List[Map[String, Any]]]]

        // Fetches excluded tag nodes of each feed
        val excludesRelType = "<<EXCLUDES>>"
        for (item <- feedNodeList) {
          val uuid = item("uuid").asInstanceOf[String]
          batchStream << Database.getChildren(uuid, excludesRelType)
        }
        val excludedTagNodeList = batchStream.execute()
          .asInstanceOf[List[List[Map[String, Any]]]]

        // Builds result
        for (i <- 0 to feedNodeList.length - 1) {
          var feedDetails: Map[String, Any] = Map(
            "id" -> feedNodeList(i)("uuid"),
            "name" -> feedNodeList(i)("name")
          )

          var includedTagList: ListBuffer[String] = ListBuffer()
          for (item <- includedTagNodeList(i)) {
            includedTagList += item("tag").asInstanceOf[String]
          }

          var excludedTagList: ListBuffer[String] = ListBuffer()
          for (item <- excludedTagNodeList(i)) {
            excludedTagList += item("tag").asInstanceOf[String]
          }

          feedDetails += "included_tag_list" -> includedTagList.toList
          feedDetails += "excluded_tag_list" -> excludedTagList.toList
          rawResult += feedDetails
        }

        result = Map(
          "status" -> true,
          "feed_list" -> rawResult.toList
        )
      } else {
        throw new Exception("User is not signed in.")
      }
    } catch {
      case e: Exception => {
        println(s"Failed to process getFeedList. Error message: $e")
        result = Map("status" -> false)
      }
    }

    result
  }

  private def createFeed(clientUuid: String,
                         name: String,
                         includedTagList: List[String],
                         excludedTagList: List[String]): Map[String, Any] = {
    var result: Map[String, Any] = null

    try {
      // Gets userUuid from session
      val future = sessionWorker ? SessionDetails(clientUuid)
      val userUuid = Await.result[Any](future, timeout.duration)
        .asInstanceOf[String]

      // Checks if user is signed in
      if (userUuid.length > 0) {
        // Checks if the feed name is unique
        seqStream << Database.getUserFeeds(userUuid)
        val feedNodeList = seqStream.execute()
          .asInstanceOf[List[List[Map[String, Any]]]](0)

        for (item <- feedNodeList) {
          val feedName = item("name").asInstanceOf[String]
          if (feedName == name) {
            throw new Exception("A feed with a given name already exists in the database.")
          }
        }

        // Creates feed node
        val modelName = "Feed"
        val relType = "<<INSTANCE>>"
        val props: Map[String, Any] = Map(
          "name" -> name
        )
        seqStream << Database.createNode(modelName, relType, props)
        val feedUuid = seqStream.execute()
          .asInstanceOf[List[Map[String, Any]]](0)("uuid").asInstanceOf[String]

        var nonExistingTagList: ListBuffer[String] = ListBuffer()

        // Fetches included tag nodes
        for (item <- includedTagList) {
          batchStream << Database.getByTag(item)
        }
        val includedTagNodeList = batchStream.execute()
          .asInstanceOf[List[Map[String, Any]]]

        // Fetches excluded tag nodes
        for (item <- excludedTagList) {
          batchStream << Database.getByTag(item)
        }
        val excludedTagNodeList = batchStream.execute()
          .asInstanceOf[List[Map[String, Any]]]

        // Prepares create relationship requests
        val includesRelType = "<<INCLUDES>>"
        for (i <- 0 to includedTagList.length - 1) {
          if (includedTagNodeList(i) != null) {
            val tagNodeUuid = includedTagNodeList(i)("uuid").asInstanceOf[String]
            batchStream << Database.createRelationship(feedUuid, tagNodeUuid, includesRelType)
          } else {
            nonExistingTagList += includedTagList(i)
          }
        }

        // Prepares create relationship requests
        val excludesRelType = "<<EXCLUDES>>"
        for (i <- 0 to excludedTagList.length - 1) {
          if (excludedTagNodeList(i) != null) {
            val tagNodeUuid = excludedTagNodeList(i)("uuid").asInstanceOf[String]
            batchStream << Database.createRelationship(feedUuid, tagNodeUuid, excludesRelType)
          } else {
            nonExistingTagList += excludedTagList(i)
          }
        }

        // Creates relationship to tag nodes
        batchStream.execute()

        result = Map(
          "status" -> true,
          "non_existing_tag_list" -> nonExistingTagList.toList
        )
      } else {
        throw new Exception("User is not signed in.")
      }
    } catch {
      case e: Exception => {
        println(s"Failed to process createFeed. Error message: $e")
        result = Map("status" -> false)
      }
    }

    result
  }

  private def processRequest(request: Map[String, Any]): Any = {
    var result: Any = null

    try {
      val coralMethodName = request("coralMethodName").asInstanceOf[String]
      val requestData = request("data").asInstanceOf[Map[String, Any]]

      println(s"Executing $coralMethodName.")

      coralMethodName match {
        case "handshake" => {
          result = handshake()
        }
        case "signIn" => {
          val clientUuid = requestData("clientUuid").asInstanceOf[String]
          val username = requestData("username").asInstanceOf[String]
          val password = requestData("password").asInstanceOf[String]
          result = signIn(clientUuid, username, password)
        }
        case "signOut" => {
          val clientUuid = requestData("clientUuid").asInstanceOf[String]
          result = signOut(clientUuid)
        }
        case "getFeedList" => {
          val clientUuid = requestData("clientUuid").asInstanceOf[String]
          result = getFeedList(clientUuid)
        }
        case "createFeed" => {
          val clientUuid = requestData("clientUuid").asInstanceOf[String]
          val name = requestData("name").asInstanceOf[String]
          val includedTagList = requestData("includedTagList").asInstanceOf[List[String]]
          val excludedTagList = requestData("excludedTagList").asInstanceOf[List[String]]
          result = createFeed(clientUuid, name, includedTagList, excludedTagList)
        }
        case _ => throw new NoSuchMethodException(coralMethodName)
      }
    } catch {
      case e: Exception => {
        println(s"Failed to process request. Error message: $e")
        result = Map("status" -> false)
      }
    }

    result
  }

  def receive = {
    case Request(uuid, request) => {
      val result = processRequest(request)
      sender ! Response(uuid, result)
    }
  }
}
