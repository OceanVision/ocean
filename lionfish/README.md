Lionfish
===

### Notes

The Lionfish server is inteded to work on a remote node. The client works as a normal class.

Exemplary usage of the **Scala-based** client:

```scala
// Initialisation
val cl = new Client
cl.connect()

// Single method execution
val rawSingleResult = cl.getByUuid("974eeacc-a07d-11e3-9f3a-2cd05ae1c39b").run()
val singleResult = rawResult.asInstanceOf[List[Map[String, Any]]]

// Using batch
val bt = cl.getBatch
bt += cl.getByLink("ContentSource", "http://www.gry-online.pl/")
bt += cl.getByUuid("974eeacc-a07d-11e3-9f3a-2cd05ae1c39b")
bt += cl.getChildren("970fc9d2-a07d-11e3-9f3a-2cd05ae1c39b", "<<INSTANCE>>")
bt += cl.getByUuid("974ee946-a07d-11e3-9f3a-2cd05ae1c39b")
val batchResult = bt.submit()

cl.disconnect()
```

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

### Code coverage (planned)

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

The table below applies to write methods: **_setProperties_**, **_createNode_**, **_deleteNode_**,
**_deleteRelationship_**

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
