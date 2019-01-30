provider "aws" {
  region = "${var.region}"
}

resource "aws_s3_bucket" "example" {
  bucket = "audio-event-bucket"
  acl = "private"
}

resource "aws_instance" "example" {
  ami = "ami-0e12cbde3e77cbb98"
  instance_type = "t2.micro"
  depends_on =["aws_s3_bucket.example"]
}

resource "aws_eip" "ip" {
  instance = "${aws_instance.example.id}"
}
