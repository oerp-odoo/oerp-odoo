HTTP Client
###########

The ``http_client`` module provides reusable components for performing HTTP
requests in a more convenient way.

It introduces persistent HTTP client profiles that define how requests should
be executed, including endpoint resolving, authentication, retry strategy.

The module is designed to be integration-agnostic and can be reused by other
modules that need to communicate with external HTTP APIs or services.

Features
========

* Configurable HTTP client profiles
* Persistent authentication configuration
* Support for multiple authentication methods
* Retry strategies for failed requests
* Support for paginated requests
* Transport layer abstraction based on ``requests`` library

HTTP Client Profiles
====================

HTTP client profiles define how requests should be performed against a remote
HTTP service.

Profiles can store configuration such as:

* Base URL
* Authentication configuration
* Retry strategy
* Response error handling policy

Profiles are intended to be reused by integrations and business modules.

Authentication
==============

The module provides a persistent authentication model that can be used directly
by HTTP client profiles.

Supported authentication methods include:

* Basic Authentication
* Bearer Token Authentication
* JWT Authentication
* Custom API Key Authentication
* Access Token Authentication
* Refresh Token Authentication

Authentication records can manage token rotation and token refresh workflows.

Retry Strategy
==============

Requests can be retried using configurable retry strategies.

Retry configuration supports defining retry behavior for transient failures and
integrates with the underlying HTTP transport layer.

Contributors
============

* Andrius Laukavičius (timefordev)
