package com.coral.workers

import java.util.UUID
import scala.concurrent.Lock
import akka.actor.Actor
import com.coral.messages._

class SessionWorker extends Actor {
  // Mapping clientUuid -> userUuid
  private var sessionMap: scala.collection.mutable.Map[String, String] =
    scala.collection.mutable.Map()
  private val writeLock = new Lock

  // Registers a new session (clientUuid -> null)
  private def registerSession(): String = {
    val newClientUuid = UUID.randomUUID().toString
    writeLock.acquire()
    sessionMap += newClientUuid -> null.asInstanceOf[String]
    writeLock.release()
    newClientUuid
  }

  // Closes the session
  private def closeSession(clientUuid: String): Boolean = {
    if (sessionMap.contains(clientUuid)) {
      sessionMap -= clientUuid
      true
    } else {
      false
    }
  }

  // Sets userUuid to the session (clientUuid -> userUuid)
  private def setUserUuid(clientUuid: String, userUuid: String): Boolean = {
    if (sessionMap.contains(clientUuid) && sessionMap(clientUuid) == null) {
      writeLock.acquire()
      sessionMap(clientUuid) = userUuid
      writeLock.release()
      true
    } else {
      false
    }
  }

  // Clears userUuid in the session
  private def clearUserUuid(clientUuid: String): Boolean = {
    if (sessionMap.contains(clientUuid) && sessionMap(clientUuid) != null) {
      writeLock.acquire()
      sessionMap(clientUuid) = null
      writeLock.release()
      true
    } else {
      false
    }
  }

  // Gets userUuid from the session
  private def getUserUuid(clientUuid: String): String = {
    if (sessionMap.contains(clientUuid) && sessionMap(clientUuid) != null) {
      sessionMap(clientUuid)
    } else {
      ""
    }
  }

  def receive = {
    case Handshake() => {
      val clientUuid = registerSession()
      sender ! clientUuid
    }
    case SessionDetails(clientUuid) => {
      val result = getUserUuid(clientUuid)
      sender ! result
    }
    case SignIn(clientUuid, userUuid) => {
      val result = setUserUuid(clientUuid, userUuid)
      sender ! result
    }
    case SignOut(clientUuid) => {
      val result = clearUserUuid(clientUuid)
      sender ! result
    }
  }
}
