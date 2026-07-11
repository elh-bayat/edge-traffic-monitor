variable "aws_region" {
  description = "AWS region"
  default     = "eu-west-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  default     = "edge-traffic-cluster"
}

variable "cluster_version" {
  description = "Kubernetes version"
  default     = "1.31"
}
