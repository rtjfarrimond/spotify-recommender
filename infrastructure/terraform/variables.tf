variable "region" {
  default = "eu-west-1"
}

variable "amis" {
  type = "map"

  default = {
    "eu-west-1" = "ami-0e12cbde3e77cbb98"
    "us-west-1" = "ami-063aa838bd7631e0b"
  }
}

variable "extractor_image" {}
variable "system_code" {}
