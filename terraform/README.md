# IoT Infrastructure configuration for the Google Cloud Platform

This `Terraform` `configuration` deploys a working Cloud infrastructure
for `IoT` devices on the **Google Cloud Platform**.

## Requirements

 * [Terraform 1.1.9+](https://www.terraform.io/downloads.html)
 * A valid **Google Cloud Platform** account

## Usage

### Setting variables

Check the [`variables.tf`](variables.tf) file for the available variables.

There are multiple ways to pass variables to `Terraform`:

 * [Command line](https://www.terraform.io/language/values/variables#variables-on-the-command-line)
 * [Values Files](https://www.terraform.io/language/values/variables#variable-definitions-tfvars-files)
 * [Environment Variables](https://www.terraform.io/language/values/variables#variable-definitions-tfvars-files)

### Deployment

Run:

```bash
$ terraform init
$ terraform apply
```

This `Terraform` `configuration` also generates some certificates:

 * A private-public key pair for the Device Registry
 * A private-public key pair for the virtual device

and retrieves the Google's CA roots from a public URL.

Certificates are stored in [`../certificates`](../certificates).
