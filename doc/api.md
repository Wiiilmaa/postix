# API Documentation

## Authentication

You need to provide an API token that refers to a valid cashdesk session by passing
the following HTTP Header:

    Authorization: Token abcdefgh1234567890

## Endpoints

The generic endpoints all implement a list view at ``/<endpoint>/`` and a detail view
at ``/<endpoint>/<id>/``. The list view supports/requires pagination.
Additionally available filters for the list view and other methods are
documented below.

The general structure of the list views looks like this:

    {
        "count": 123,
        "next": "http://<url>/api/<endpoint>/?page=2",
        "previous": null,
        "results": [
            ...
        ]
    }

### Transaction

``/api/transactions/``

Lists all past transactions.

Sample result: (TODO)

#### Creating a transaction

To create a transaction you need to send a ``POST`` request to ``/api/transactions/`` that
contains a list of transaction positions that you want to create. Example:

    {
        "cash_given": "12.00",
        "positions": [
            {
                "type": "redeem",
                "secret": "abcdefgh"
            },
            {
                "type": "sell",
                "product": 1,
                "authorized_by": "12345"
            }
        ]
    }
    
You will receive an answer that could look like this:

    {
        "success": false,
        "positions": [
            {
                "success": false,
                "message": "This ticket can only be redeemed by persons on the \"CCC Members\" list",
                "type": "input",
                "missing_field": "list_3"
            },
            {
                "success": true
            }
        ]
    }
  
The first-level ``success`` attribute tells you whether the transaction was successful or
not. If this is ``false``, nothing has been written to the database. The HTTP status code will 
be 201 if ``success`` is ``true`` and 400 otherwise.

The ``positions`` list contains the result for the single positions in the same order you specified them. 
If a position was unsuccessful you will be given a human-readable reason, and - if the issue can be resolved - a
type. Currently, the following types can be returned:

* ``"input"``: This tells you that you should prompt the user for entering a value (normally an ID
  of a ListConstraintEntry). If you retry the transaction, you should include the input as an additional
  attribute of the position with the name given in ``missing_field``.
  
* ``"confirmation"``: This tells you that you should prompt the user to confirm a message, e.g. a warning.
  If you retry the transaction, you should include an attribute of value ``true`` with the name given in
  ``missing_field``.
  
* ``None``: This is an error message that you cannot do anything about.

#### Reversing a transaction

To reverse a whole transaction, just issue a POST request to ``/api/transactions/12345/reverse/``. You will
receive a 200 status code on success and a 400 status code (with an error in the response body) otherwise.

### Preorders

``/api/preorders/``

Only available to admin users. 

Sample result object (embedded in pagination as described abobe):

    {
        "order_code": "12346",
        "is_paid": true,
        "warning_text": "",
        "positions": [
            {
                "id": 1,
                "preorder": 1,
                "secret": "abcde",
                "product": 1
            },
            {
                "id": 2,
                "preorder": 1,
                "secret": "efghij",
                "product": 1
            }
        ]
    }


### Preorder positions

``/api/preorderpositions/``

This list view *requires* that you specify the query parameter ``secret``
to search for a specific positions. If you do not specify this parameter,
an empty result will be returned.

Sample result object (embedded in pagination as described abobe):

    {
        "id": 1,
        "preorder": 1,
        "secret": "abcde",
        "product": 1
    }

### List constraints

``/api/listconstraints/``

Lists all possible lists that are used for list constraints.

Sample result object (embedded in pagination as described abobe):

    {
        "id": 1,
        "name": "CCC-Mitglied"
    }
  
### List constraint entries

``/api/listconstraintentries/``

Lists the entries in a list constraint.

This list view *requires* that you specify the query parameter ``listid``
with the ID of a list constraint **and** the query parameter ``search`` 
with at least three characters of a search query that will be used to look
up a specific entry.
If you do not specify these two parameters, an empty result will be returned.

Sample result object (embedded in pagination as described abobe):

    {
        "id": 1,
        "name": "Rainer Zufall",
        "identifier": "12345"
    }
