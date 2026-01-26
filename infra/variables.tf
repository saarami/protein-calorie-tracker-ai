variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "project_name" {
  type = string
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "ssh_ingress_cidr" {
  type = string
}

variable "ec2_key_name" {
  type = string
}

variable "repo_ssh_url" {
  type = string
}

variable "ssm_path_prefix" {
  type = string
}
