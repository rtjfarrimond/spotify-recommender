# data "aws_ecs_task_definition" "extractor" {
#   task_definition = "${aws_ecs_task_definition.extractor.family}"
#   depends_on      = ["aws_ecs_task_definition.extractor"]
# }
# 
# data "aws_iam_role" "ecs_task_execution_role" {
#   name = "ecsTaskExecutionRole"
# }
# 
# resource "aws_ecr_repository" "spot-rec-ecr" {
#   name = "${var.system_code}-${var.extractor_image}"
# }
# 
# resource "aws_ecs_cluster" "spot-rec-ecs-cluster" {
#   name = "${var.system_code}-ecs-cluster"
# }
# 
# resource "aws_ecs_task_definition" "extractor" {
#   family                   = "${var.system_code}-${var.extractor_image}-nginx"
#   requires_compatibilities = ["FARGATE"]
#   network_mode             = "awsvpc"
#   cpu                      = 256
#   memory                   = 512
#   execution_role_arn       = "${data.aws_iam_role.ecs_task_execution_role.arn}"
# 
#   container_definitions = <<EOF
# [
#   {
#     "environment": [{
#       "name": "SECRET",
#       "value": "KEY"
#     }],
#     "essential": true,
#     "image": "479503948477.dkr.ecr.eu-west-1.amazonaws.com/test-repo:latest",
#     "memoryReservation": 384,
#     "name": "test-repo",
#     "logConfiguration": {
#       "logDriver": "awslogs",
#       "options": {
#         "awslogs-group": "${aws_cloudwatch_log_group.spot-rec-log-group.name}",
#         "awslogs-region": "${var.region}",
#         "awslogs-stream-prefix": "ecs"
#       },
#       "portMappings": [
#         {
#           "containerPort": 80,
#           "hostPort": 80,
#           "protocol": "tcp"
#         }
#       ]
#     }
#   }
# ]
# EOF
# }
# 
# resource "aws_ecs_service" "extractor-service" {
#   name          = "${var.extractor_image}-service"
#   cluster       = "${aws_ecs_cluster.spot-rec-ecs-cluster.id}"
#   desired_count = 1
#   launch_type   = "FARGATE"
# 
#   task_definition = "${aws_ecs_task_definition.extractor.family}:${max("${aws_ecs_task_definition.extractor.revision}", "${data.aws_ecs_task_definition.extractor.revision}")}"
# 
#   network_configuration {
#     subnets = ["${var.subnet_id}"]
#     assign_public_ip = true
#   }
# 
# }
# 
# output "ecr_repo_uri" {
#   value = "${aws_ecr_repository.spot-rec-ecr.repository_url}"
# }

