Lionfish
===

### Running

Temporarily you will need to copy neo4j.app jars to lib folder.

http://mvnrepository.com/artifact/org.neo4j.app/neo4j-server/2.0.2

Then you can run 

`./run.sh -p 7777`

Later you will be able to configure GraphDB path, whether to run the REST
console and REST console port

### Scala-based client

The Lionfish client works as a normal package. In order to use the client, you might build a _.jar_
package of the Lionfish project and import the client classes:

```scala
import com.lionfish.client._
```

As the Scala-based client has changed recently, it requires some description. Current implementation
involves streams which are responsible for processing and sending requests. The client is now
divided into three significant parts:

* _Database_ - the object which contains Lionfish methods implemented as case classes
* _SequenceStream_ - the class which is responsible for processing a sequence of Lionfish methods,
it guarantees methods are executed in natural order
* _BatchStream_ - the class whose job is to process a batch of Lionfish methods, it might be
significantly faster than _SequenceStream_ in dealing with large requests, however it **does not**
ensure methods are executed in natural order

You can use a stream (both _SequenceStream_ and _BatchStream_) in this way:

```scala
val seqStream = Database.getSequenceStream
seqStream << Database.getByUuid("97746a22-a07d-11e3-9f3a-2cd05ae1c39b")
val result = seqStream.execute()
```

It is not the only possible usage. If you don't like writing an additional line of code in order to
commit a request, you might do it as you wish:

```scala
val batchStream = Database.getBatchStream
val result = batchStream !! Database.getByUuid("97746a22-a07d-11e3-9f3a-2cd05ae1c39b")
```

Moreover, you are able to chain different methods within one request:

```scala
val batchStream = Database.getBatchStream
batchStream << (Database.getByUuid("97746a22-a07d-11e3-9f3a-2cd05ae1c39b")
  << Database.getByLink("ContentSource", "http://www.gry-online.pl/"))
val result = batchStream.execute()
```

```scala
val seqStream = Database.getSequenceStream
val result = (seqStream
  !! (Database.getByUuid("97746a22-a07d-11e3-9f3a-2cd05ae1c39b")
  << Database.getByLink("ContentSource", "http://www.gry-online.pl/")))
```

### Python-based client

Exemplary usage of the **Python-based** client:

```python
# Initialisation
cl = Client()
cl.connect()

# Single method execution
single_result = cl.get_by_uuid('974eeacc-a07d-11e3-9f3a-2cd05ae1c39b')

# Using batch
bt = cl.get_batch()
bt.append(cl.getByLink, 'ContentSource', 'http://www.gry-online.pl/')
bt.append(cl.getByUuid, '974eeacc-a07d-11e3-9f3a-2cd05ae1c39b')
bt.append(cl.get_children, '970fc9d2-a07d-11e3-9f3a-2cd05ae1c39b', '<<INSTANCE>>')
bt.append(cl.getByUuid, '974ee946-a07d-11e3-9f3a-2cd05ae1c39b')
batch_result = bt.submit()

cl.disconnect()
```

### Code coverage

Each test case of the set 1 examines one method.

#### Set 1.1

The table below applies to read methods: **_getByUuid_**, **_getByLink_**, **_getModelNodes_**

| using batch | non-empty output expected |
| :---------: | :-----------------------: |
| no  | yes |
| no  | no  |
| yes | yes |
| yes | no  |

#### Set 1.2

The table below applies to read methods: **_getChildren_**, **_getInstances_**

| using batch | non-empty output expected | non-empty props |
| :---------: | :-----------------------: | :-------------: |
| no  | yes | no  |
| no  | no  | yes |
| yes | yes | yes |
| yes | no  | no  |

#### Set 1.3

The table below applies to write methods: **_setProperties_**, **_deleteProperties_**,
**_createNode_**, **_deleteNode_**, **_deleteRelationship_**, **_setRelationshipProperties_**,
**_deleteRelationshipProperties_**

| using batch | correct input |
| :---------: | :-----------: |
| no  | yes |
| no  | no  |
| yes | yes |
| yes | no  |

#### Set 1.4

The table below applies to write method: **_createRelationship_**

| using batch | correct input | non-empty props |
| :---------: | :-----------: | :-------------: |
| no  | yes | no  |
| no  | no  | yes |
| yes | yes | yes |
| yes | no  | no  |

***

Each test case of the set 2 examines more than one method. Some cases use batch. The purpose of this set
is to test a convergence of results given by different methods.

The tables below present mandatory methods to be tested in each test case. Nevertheless there might
be used other methods from the set 2 in some test cases.

#### Set 2.1

The table below applies to all available methods.

| method / test case     | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| :--------------------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| _getByUuid_            | No  | Yes | No  | Yes | No  | Yes | Yes |
| _getByLink_            | No  | No  | Yes | Yes | No  | Yes | Yes |
| _getModelNodes_        | Yes | No  | No  | Yes | Yes | No  | No  |
| _getChildren_          | Yes | No  | No  | Yes | Yes | No  | No  |
| _getInstances_         | Yes | Yes | Yes | No  | No  | Yes | No  |
| _createNode_           | Yes | No  | No  | No  | Yes | No  | Yes |
| _createRelationship_   | Yes | Yes | No  | No  | No  | No  | Yes |
| _deleteNode_           | Yes | Yes | No  | Yes | No  | Yes | No  |
| _deleteRelationship_   | No  | No  | Yes | Yes | Yes | Yes | Yes |

#### Set 2.2

The table below applies to some read methods mixed with _setProperties_.

| method / test case    | 1 | 2 |
| :-------------------: | :---: | :---: |
| _getByUuid_           | No  | Yes |
| _getChildren_         | Yes | No  |
| _setProperties_       | Yes | Yes |
