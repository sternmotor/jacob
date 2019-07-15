# Software defined networking

## [Example](https://medium.com/@henriksylvesterpedersen/you-dont-need-that-bastion-host-cd1b1717a9e7)
Modern software defined networking is really under appreciated. Think about your VPC’s, subnets and Network ACL’s for each subnet. Apply Security groups liberally but be stringent with permissions. Limit the scope of all IAM policies provided by IAM Roles (If I had a dime for every time I see FullS3 attached to an IAM role on all webservers).

We have a default Network ACL on all production environments that limit all inbound traffic to only port 80, 443, 22 and ICMP. We also allow TCP 32768–61000 inbound because ACL’s are stateless and Linux needs the upper port range for Ephemeral ports. We allow all traffic in our private subnet in our Network ACL for easy every day use, it only serves as a last line of defence against the internet in case our security groups get opened or otherwise disabled. Outbound to the internet we are very specific about what we allow and generally only allow HTTP/HTTPS + ICMP as that’s all that we need for updates and API calls.

We further lock down communication between instances by applying Security groups as needed, where we e.g. open port 3306 on members of the “database security group” up to members of the “web app security group”.

Our setup defers when it comes to SSH. We have no opening for SSH anyway except in our Network ACL. If you try to SSH to our instance IP’s (which are also hidden by the ELB), you will be met with absolutely nothing. Zero. You can’t ping them, and you can’t SSH. Nothing is open to the public internet.

We have a single security group that all servers are member of, called “SSH access list”. This group has been manually setup, but is managed automatically using a CLI tool we’ve developed in-house and that is part of our primary project.

This CLI tool opens up your current IP (or a specific IP / Subnet you provide) for 12 hours. The next time somebody runs this tool, it will scan for old IP allowances and remove them. The tool can also clear the access list.

It works using the AWS API, and uses a static token in our project, that is limited to only a few actions and only on this specific Security Group. It can’t open port 80, it can’t add another group, it can’t even delete the current group. It can only add and remove rules on port 22 on this specific Security Group. 




