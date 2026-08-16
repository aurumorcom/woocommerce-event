# C1 System Context: WordPress Kafka Event Bridge (wordpress-kafka)

```mermaid
erDiagram
    WordPressKafkaEventBridge {
        string service_name "WordPressKafkaEventBridge"
        string environment "Production / Staging"
        string version "1.0.0"
        string role "Domain Facade & Application Logic (Repo 2)"
    }

    WordPressWooCommerceRESTApi {
        string endpoint "/wp-json/wc/v3"
        string auth_type "OAuth1.0a / BasicAuth"
        string status "External Black Box"
    }

    ApacheKafkaCluster {
        string cluster_id "kafka-cluster-prod"
        string broker_nodes "kafka-1:9092,kafka-2:9092"
    }

    RisingWaveStreamingEngine {
        string engine_type "RisingWave"
        string features "Idempotency, Normalization, Watermarking"
        string sql_endpoint "postgres://root@risingwave:4566/dev"
    }

    PythonKafkaSDK {
        string dependency "python-kafka (Repo 1)"
        string role "Infrastructure SDK"
    }

    WordPressKafkaEventBridge ||--|| PythonKafkaSDK : "Imports and Configures"
    WordPressWooCommerceRESTApi ||--o{ WordPressKafkaEventBridge : "Synchronous HTTP REST Calls / Inbound Webhooks"
    WordPressKafkaEventBridge ||--o{ ApacheKafkaCluster : "Produces Inbound Webhook Events via SDK"
    RisingWaveStreamingEngine ||--o{ WordPressKafkaEventBridge : "Pushes Normalized & Deduplicated Events via HTTP Sinks"