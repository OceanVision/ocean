Coral
===

### Webservice operations

There are several operations under development. They are accessible by sending a HTTP request to:

```
http://ocean-coral.no-ip.biz:14/<operation_path>
```

All these operations take a **json object** as a parameter which travels in a HTTP request body message.

***

The methods returns (in a HTTP response) a serialised **object**:

```ruby
{ key1: value1, key2: value2 }
```

***

The whole communication begins when the client requests a handshake. It may be performed by a special operation:

#### handshake

Returned value: **object**

Returned value contains keys:
* _status_ `bool`
* _client_id_ `string`

***

When the client ID is assigned, then the client service is eligible to perform other requests:

#### sign_in

Parameter contains keys:
* _client_id_ `string`
* _username_ `string`
* _password_ `string`

Returned value: **object**

Returned value contains keys:
* _status_ `bool`

#### sign_out

Parameter contains keys:
* _client_id_ `string`

Returned value: **object**

Returned value contains keys:
* _status_ `bool`

#### get_article_list

Parameter contains keys:
* _last_news_id_ `string`
* _count_ `int`
* _feed_id_ `string`
* _client_id_ `string`

Returned value: **object**

Returned value contains keys:
* _status_ `bool`
* _article_list_ `list[object]`

Each element of _article_list_ contains keys:
* _article_id_ `string`
* _link_ `string`
* _author_ `string`
* _title_ `string`
* _time_ `int`
* _description_ `string`
* _image_source_ `string`

#### get_article_details

Parameter contains keys:
* _client_id_ `string`
* _article_id_ `string`

Returned value: **object**

Returned value contains keys:
* _status_ `bool`
* _article_id_ `string`
* _body_ `string`

#### get_feed_list

Parameter contains keys:
* _client_id_ `string`

Returned value: **object**

Returned value contains keys:
* _status_ `bool`
* _feed_list_ `list[object]`

Each element of _feed_list_ contains keys:
* _id_ `string`
* _name_ `string`
* _included_tag_list_ `list[string]`
* _excluded_tag_list_ `list[string]`

#### create_feed

Parameter contains keys:
* _client_id_ `string`
* _name_ `string`
* _included_tag_list_ `list[string]`
* _excluded_tag_list_ `list[string]`

Returned value: **object**

Returned value contains keys:
* _status_ `bool`
* _non_existing_tag_list_ `list[string]`

