module "vpc" {
  source = "./modules/vpc"

  project_name     = var.project_name
  environment      = var.environment
  ssh_ingress_cidr = var.ssh_ingress_cidr
}

module "ec2" {
  source = "./modules/ec2"

  project_name          = var.project_name
  environment           = var.environment
  public_subnet_id      = module.vpc.public_subnet_id
  ec2_security_group_id = module.vpc.ec2_security_group_id

  key_name        = var.ec2_key_name
  repo_ssh_url    = var.repo_ssh_url
  ssm_path_prefix = var.ssm_path_prefix
  app_port        = 8001
}
