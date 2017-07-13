provider "aws"{
  access_key="${var.access_key}"
  secret_key="${var.secret_key}"
  region="${var.region}"
}

resource "aws_iam_user" "playground" {
  name = "playground99"
  path = "/home/playground99/"
}

resource "aws_iam_access_key" "playground" {
  user  = "${aws_iam_user.playground.name}"
}

resource "aws_key_pair" "playground" {
  key_name   = "playground"
  public_key = "${file("/Users/Mourad/.ssh/id_rsa.pub")}"
}



resource "aws_vpc" "playground" {
  cidr_block = "10.0.1.0/24"
}


resource "aws_default_security_group" "playground-default" {
  vpc_id = "${aws_vpc.playground.id}"

  ingress {
    protocol  = -1
    self      = true
    from_port = 0
    to_port   = 0
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_subnet" "playground-subnet" {
  vpc_id     = "${aws_vpc.playground.id}"
  cidr_block ="10.0.1.0/24"
  map_public_ip_on_launch = true

}



resource "aws_instance" "lab"{
  ami = "ami-6d48500b"
  instance_type = "t2.micro"
  subnet_id="${aws_subnet.playground-subnet.id}"
}

output "public_ip"{
  value = "${aws_instance.lab.public_ip}"
}
