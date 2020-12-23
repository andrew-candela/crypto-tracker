resource aws_db_instance crypto_db {
  identifier                            = "crypto-tracker"
  instance_class                        = "db.t2.micro"
  allocated_storage                     = 20
  engine                                = "postgres"
  engine_version                        = 11.5
  multi_az                              = false
  option_group_name                     = "default:postgres-11"
  parameter_group_name                  = "default.postgres11"
  port                                  = var.PG_PORT
  publicly_accessible                   = true
  skip_final_snapshot                   = true
  storage_encrypted                     = false
  storage_type                          = "gp2"
  username                              = var.PG_USER
  password                              = var.PG_PASSWORD
  name                                  = var.PG_DATABASE
  db_subnet_group_name                  = aws_db_subnet_group.crypto_db.name
  vpc_security_group_ids                = [aws_security_group.wide_open.id]

  tags = {Application = "crypto-tracker"}
}

resource aws_vpc base {
    cidr_block = "172.32.0.0/16"
    enable_dns_hostnames = true 
    enable_classiclink_dns_support = false
    tags = {
        Name = "crypto-tracker"
    }
}

resource aws_security_group wide_open {
    name = "wide-open-db-ingress"
    description = "managed by TF - allow DB access from any IP"
    vpc_id = aws_vpc.base.id
    ingress {
        description = "all db ingress"
        protocol = "tcp"
        from_port = 5432
        to_port = 5432
        cidr_blocks = ["0.0.0.0/0"]
    }
    egress {
        description = "all traffic egress"
        protocol = -1
        from_port = 0
        to_port = 0
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_subnet" "us_west_2a" {
  vpc_id     = aws_vpc.base.id
  cidr_block = "172.32.0.0/20"
  availability_zone = "us-west-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "crypto-tracker"
  }
}

resource "aws_subnet" "us_west_2b" {
  vpc_id     = aws_vpc.base.id
  cidr_block = "172.32.16.0/20"
  availability_zone = "us-west-2b"
  map_public_ip_on_launch = true

  tags = {
    Name = "crypto-tracker"
  }
}

resource aws_db_subnet_group crypto_db {
    name = "crypto-db"
    description = "TF managed subnets for crypto DB"
    subnet_ids = [aws_subnet.us_west_2a.id, aws_subnet.us_west_2b.id]
}

resource aws_internet_gateway igw {
    vpc_id = aws_vpc.base.id
    tags = {
        Name = "base-igw"
    }
}

resource aws_route_table crypto_internet {
    vpc_id = aws_vpc.base.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw.id
    }
    tags = {
        Name = "crypto-route-table"
    }
}

resource aws_route_table_association a {
    subnet_id = aws_subnet.us_west_2a.id
    route_table_id = aws_route_table.crypto_internet.id
}

resource aws_route_table_association b {
    subnet_id = aws_subnet.us_west_2b.id
    route_table_id = aws_route_table.crypto_internet.id
}