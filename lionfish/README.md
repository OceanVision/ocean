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
bt.append(cl.getByLink("ContentSource", "http://www.gry-online.pl/"))
bt.append(cl.getByUuid("974eeacc-a07d-11e3-9f3a-2cd05ae1c39b"))
bt.append(cl.getInstances("Content"))
bt.append(cl.getByUuid("974ee946-a07d-11e3-9f3a-2cd05ae1c39b"))
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
bt.append(cl.get_instances, 'Content')
bt.append(cl.getByUuid, '974ee946-a07d-11e3-9f3a-2cd05ae1c39b')
batch_result = bt.submit()

cl.disconnect()
```

### Code coverage (planned)

Each test case of the set 1 examines one method.

#### Set 1.1

The table below applies to read methods: **_getByUuid_**, **_getByLink_**, **_getModelNodes_**, **_getChildren_**,
**_getInstances_**

| using batch | non-empty output expected |
| :---------: | :-----------------------: |
| no  | yes |
| no  | no  |
| yes | yes |
| yes | no  |

#### Set 1.2

The table below applies to write methods: **_set_**, **_createNode_**, **_deleteNode_**, **_createRelationship_**,
**_deleteRelationship_**

| using batch | correct input |
| :---------: | :-----------: |
| no  | yes |
| no  | no  |
| yes | yes |
| yes | no  |

***

Each test case of the set 2 examines more than one method. Some cases use batch. The purpose of this set
is to test a convergence of results given by different methods.

#### Set 2.1

The table below applies to read methods.

| method / test case     | 1 | 2 | 3 | 4 | 5 | 6 |
| :--------------------- | :---: | :---: | :---: | :---: | :---: | :---: |
| _getByUuid_            | No  | Yes | No  | Yes | No  | Yes |
| _getByLink_            | No  | No  | Yes | Yes | No  | Yes |
| _getModelNodes_        | Yes | No  | No  | Yes | Yes | No  |
| _getChildren_          | Yes | No  | No  | Yes | Yes | No  |
| _getInstances_         | Yes | Yes | No  | No  | No  | Yes |

#### Set 2.2

The table below applies to write methods.

| method / test case     | 1 | 2 | 3 | 4 | 5 |
| :--------------------- | :---: | :---: | :---: | :---: | :---: |
| _createNode_           | No  | No  | Yes | Yes | Yes |
| _deleteNode_           | Yes | No  | Yes | No  | Yes |
| _createRelationship_   | Yes | No  | No  | Yes | Yes |
| _deleteRelationship_   | No  | Yes | No  | No  | Yes |

#### Set 2.3

The table below applies to some read methods mixed with _set_.

| method / test case     | 1 | 2 |
| :--------------------- | :---: | :---: |
| _getByUuid_           | No  | Yes |
| _getChildren_         | Yes | No  |
| _set_                 | Yes | Yes |
