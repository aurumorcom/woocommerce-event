# C2 Container Architecture: WordPress Kafka Event Bridge

```mermaid
erDiagram
    WindmillExecutionEngine {
        string service_name "Windmill Script Execution Engine"
        string runtime "Python 3.11 / Pydantic v2"
    }

    WindmillInboundScript {
        string script_path "apps/wordpress-kafka-api/f/wordpress-kafka/*.py"
        string action "Receive Webhook -> Parse Pydantic -> Serialize Avro -> Publish Kafka"
    }

    WindmillOutboundScript {
        string script_path "apps/wordpress-kafka-api/f/wordpress-kafka/*.py"
        string action "Receive RW Sink Push -> Call WooCommerce REST -> Publish Ack to Kafka"
    }

    WooCommerceHttpClient {
        string base_url "https://store.example.com/wp-json/wc/v3"
        string auth "OAuth1.0a / BasicAuth"
    }

    PythonKafkaSDK_Middleware {
        string role "Idempotency & Deduplication Engine"
        string source "python-kafka"
    }

    WindmillExecutionEngine ||--|| WindmillInboundScript : "Executes Inbound Scripts"
    WindmillExecutionEngine ||--|| WindmillOutboundScript : "Executes Outbound Scripts"
    WindmillInboundScript ||--|| PythonKafkaSDK_Middleware : "Uses SDK for translation & publishing"
    WindmillOutboundScript ||--|| PythonKafkaSDK_Middleware : "Uses SDK for idempotency checks"
    WindmillOutboundScript ||--|| WooCommerceHttpClient : "Dispatches REST API Request"