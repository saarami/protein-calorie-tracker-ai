variable "project_name" { type = string }
variable "environment"  { type = string }

variable "public_subnet_id" {
  type = string
}

variable "ec2_security_group_id" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "key_name" {
  type = string
}

variable "repo_ssh_url" {
  type = string
}

variable "app_port" {
  type    = number
  default = 8001
}

variable "ssm_path_prefix" {
  type = string
  # example: /protein-calorie-tracker/dev
}
