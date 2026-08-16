# 7. Deployment View

## 7.1 Infrastructure & Topology Map

```mermaid
erDiagram
    KubernetesCluster {
        string cluster_name "k8s-prod-cluster"
        string namespace "wordpress-facade-prod"
    }

    WindmillEnginePod {
        string image "windmill/windmill-server:latest"
        string port "8000"
    }

    KafkaBrokerPod {
        string image "confluentinc/cp-kafka:latest"
        string port "9092"
    }

    SchemaRegistryPod {
        string image "confluentinc/cp-schema-registry:latest"
        string port "8081"
    }

    RisingWavePod {
        string image "risingwavelabs/risingwave:latest"
        string port "4566"
    }

    PostgreSQLPod {
        string image "postgres:16-alpine"
        string port "5432"
    }

    KubernetesCluster ||--o{ WindmillEnginePod : "Deploys Deployment"
    KubernetesCluster ||--o{ KafkaBrokerPod : "Deploys StatefulSet"
    KubernetesCluster ||--o{ SchemaRegistryPod : "Deploys Deployment"
    KubernetesCluster ||--o{ RisingWavePod : "Deploys StatefulSet"
    KubernetesCluster ||--o{ PostgreSQLPod : "Deploys StatefulSet"
```

## 7.2 Port and Protocol Allocation
| Node / Service | Internal Port | External Port | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `wordpress-facade` | 8000 | 443 (Ingress) | HTTP/REST | Inbound Webhooks & RW Push Receiver |
| `kafka-broker` | 9092 | 9092 | TCP/Kafka | Message Streaming Transport |
| `schema-registry` | 8081 | 8081 | HTTP/REST | Avro Schema Registration |
| `risingwave` | 4566 | 4566 | PostgreSQL Wire | SQL Query & Stream Topology Management |
| `postgres` | 5432 | 5432 | PostgreSQL Wire | Facade Outbox & Idempotency Storage |
