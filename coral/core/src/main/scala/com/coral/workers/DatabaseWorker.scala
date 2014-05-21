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
  private val batchStream: List[Stream] = List(Database.getBatchStream, Database.getBatchStream)

  private def handshake(): Map[String, Any] = {
    var result: Map[String, Any] = null

    try {
      val future = sessionWorker ? Handshake()
      val clientUuid = Await.result[Any](future, timeout.duration)
        .asInstanceOf[String]

      result = Map("client_id" -> clientUuid)
    } catch {
      case e: Exception => {
        println(s"Failed to process handshake. Error message: $e")
        result = Map()
      }
    }

    result
  }

  private def signIn(clientUuid: String, username: String, password: String): Map[String, Any] = {
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
        result = Map("status" -> false)
      }
    } catch {
      case e: Exception => {
        println(s"Failed to process signIn. Error message: $e")
        result = Map()
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
        result = Map()
      }
    }

    result
  }

  private def getFeedList(clientUuid: String): Map[String, Any] = {
    var result: Map[String, Any] = null

    try {
      val future = sessionWorker ? SessionDetails(clientUuid)
      val userUuid = Await.result[Any](future, timeout.duration)
        .asInstanceOf[String]

      // Checks if user is signed in
      if (userUuid.length > 0) {
        val rawResult: ListBuffer[Map[String, Any]] = ListBuffer()

        // Fetches feed nodes
        seqStream << Database.getUserFeeds(userUuid)
        val feedList = seqStream.execute()
          .asInstanceOf[List[List[Map[String, Any]]]](0)

        // Fetches included tag nodes of each feed
        val includesRelType = "<<INCLUDES>>"
        val excludesRelType = "<<EXCLUDES>>"

        for (item <- feedList) {
          val uuid = item("uuid").asInstanceOf[String]
          batchStream(0) << Database.getChildren(uuid, includesRelType)
          batchStream(1) << Database.getChildren(uuid, excludesRelType)
        }

        val includedTagNodeList = batchStream(0).execute()
          .asInstanceOf[List[List[Map[String, Any]]]]

        val excludedTagNodeList = batchStream(1).execute()
          .asInstanceOf[List[List[Map[String, Any]]]]

        // Builds result
        for (i <- 0 to feedList.length - 1) {
          var feedDetails: Map[String, Any] = Map(
            "id" -> feedList(i)("uuid"),
            "name" -> feedList(i)("name")
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

        result = Map("feed_list" -> rawResult.toList)
      } else {
        result = Map()
      }
    } catch {
      case e: Exception => {
        println(s"Failed to process getFeedList. Error message: $e")
        result = Map()
      }
    }

    result
  }

  private def processRequest(request: Map[String, Any]): Any = {
    val coralMethodName = request("coralMethodName").asInstanceOf[String]
    val requestData = request("data").asInstanceOf[Map[String, Any]]

    println(s"Executing $coralMethodName.")

    var result: Any = null
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
