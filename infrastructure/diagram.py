from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Fargate
from diagrams.aws.security import IAM
from diagrams.aws.storage import S3


with Diagram("NCCID Infrastructure Outline", show=False, direction="LR"):
    with Cluster("IAM Groups"):
        ts = IAM("Training Access")
        vs = IAM("Validation Access")
        etl = IAM("ETL Access")
        audit = IAM("Audit Access")
        uploader = IAM("Data provider")
    warehouse = S3("ImageStorage")
    inventory = S3("Inventory")
    objectlog = S3("Object Log")
    warehouse >> inventory
    warehouse >> objectlog

    ts >> Edge(style="dashed") >> warehouse
    vs >> Edge(style="dashed") >> warehouse
    audit >> Edge(style="dashed") >> objectlog
    uploader >> warehouse
    fg = Fargate("Pipeline Tasks")
    etl >> Edge(style="dotted") >> fg >> warehouse
    fg >> Edge(style="dashed") >> inventory
