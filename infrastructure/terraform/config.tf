provider "aws" {
  region = "${var.region}"
}

resource "aws_s3_bucket" "example" {
  bucket = "audio-event-bucket"
  acl = "private"
}

output "s3_domain" {
  value = "${aws_s3_bucket.example.bucket_domain_name}"
}

resource "aws_instance" "example" {
  ami = "${lookup(var.amis, var.region)}"
  instance_type = "t2.micro"
  depends_on =["aws_s3_bucket.example"]
}

resource "aws_eip" "ip" {
  instance = "${aws_instance.example.id}"
}

output "ip" {
  value = "${aws_eip.ip.public_ip}"
}
