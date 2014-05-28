package com.lionfish.wrappers

import org.neo4j.graphdb.{Relationship, Node}

trait DatabaseWrapper {
  def init()

  protected def parseMap(node: Node): Map[String, Any]
  protected def parseMap(rel: Relationship): Map[String, Any]
  protected def parseSet(node: Node): Set[(String, Any)]
  protected def parseSet(rel: Relationship): Set[(String, Any)]

  def executeQuery(args: List[Map[String, Any]]): List[Any]
  def getByUuid(args: List[Map[String, Any]]): List[Any]
  def getByLink(args: List[Map[String, Any]]): List[Any]
  def getByTag(args: List[Map[String, Any]]): List[Any]
  def getByUsername(args: List[Map[String, Any]]): List[Any]
  def getByLabel(args: List[Map[String, Any]]): List[Any]
  def getModelNodes(args: List[Map[String, Any]]): List[Any]
  def getChildren(args: List[Map[String, Any]]): List[Any]
  def getInstances(args: List[Map[String, Any]]): List[Any]
  def getUserFeeds(args: List[Map[String, Any]]): List[Any]
  def setLabel(args: List[Map[String, Any]]): List[Any]
  def deleteLabel(args: List[Map[String, Any]]): List[Any]
  def setProperties(args: List[Map[String, Any]]): List[Any]
  def deleteProperties(args: List[Map[String, Any]]): List[Any]
  def setRelationshipProperties(args: List[Map[String, Any]]): List[Any]
  def deleteRelationshipProperties(args: List[Map[String, Any]]): List[Any]
  def createModelNodes(args: List[Map[String, Any]]): List[Any]
  def createNodes(args: List[Map[String, Any]]): List[Any]
  def deleteNodes(args: List[Map[String, Any]]): List[Any]
  def createRelationships(args: List[Map[String, Any]]): List[Any]
  def createUniqueRelationships(args: List[Map[String, Any]]): List[Any]
  def deleteRelationships(args: List[Map[String, Any]]): List[Any]
}
