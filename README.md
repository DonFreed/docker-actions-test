# Example usage of the Sentieon software running on GitHub Actions for pipeline CI/CD

### Background

The Sentieon software requires a license to run. In this repository, we show how Sentieon's [license server extension](https://support.sentieon.com/appnotes/license_server/) functionality can be combined with GitHub Action's [encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) to provide a license to the Sentieon software inside a GitHub Actions runner.

For license security, this solution relies on a secure encryption key that is shared by the runner and the Sentieon license server. The runner sends the license server a message that is encrypted by the key. The license server uses the same key to decrypt the ciphertext and check the message contents against an expected text.

### Step 1 - Generate an encryption key

The following command can be used to generate an encryption key and print the base64 encoded key to the terminal:
```
python3 .github/scripts/license_message.py generate_key
```

The base64 encoded key can then be added as an actions secret in the GitHub web interface with the name `ENCRYPTION_KEY`.

### Step 2 - Setup of the Sentieon license server

A machine should be started that can host the Sentieon license server. This machine should allow inbound TCP communication at the desiginated port from all inbound IP addresses and will need to allow outbound HTTPS communication with the internet for license validation.

Once the machine is started, you will need to obtain a Sentieon license that can be bound to the machine's internal (private) IP address and the port that was opened. The Sentieon software will need to be downloaded to this machine and this machine also needs the `license_extension.py` and `.github/scripts/license_message.py` scripts from this repository. The encryption key will also need to be moved to this machine; the `license_extension.py` script expects to find the base64 encoded key at `~/.sentieon/license_key.txt`.

Once these requirements are satisfied, you can start the Sentieon license server on this machine with the following command:
```
<path/to/bin>/sentieon licsrvr --start --auth ./license_extension.py <license_file>
```
The license server should start on this machine and will use the `license_extension.py` script to authenticate inbound license requests.

### Step 3 - Add additional secrets to GitHub Actions

We need to add additional secrets with information on the license server setup. We can create a `LICSRVR_IP` secret with the license server's public IP address and port in the format, `<public_IP>:<port>`. We can also create a `LICENSE_MESSAGE` secret, with the message text expected by the license server (`Secret message`, in our example).

### Step 4 - Setup a workflow in GitHub Actions

We are now ready to use the Sentieon software within GitHub Actions. An example workflow is provided at `.github/workflows/docker_build.yml`. The example workflow downloads a small test reference genome and sequence dataset and the Sentieon software to the runner. It uses the script at `.github/scripts/license_message.py` to generate an encrypted message from the `ENCRYPTION_KEY` and `LICENSE_MESSAGE` secrets, and passes the encrypted message to the Sentieon software through the `SENTIEON_AUTH_DATA` variable. The `SENTIEON_LICENSE` variable is populated directly by the `LICSRVR_IP` secret. After setting the appropriate license information, this workflow performs read alignment and sorting.

### Future work

This solution relies on secrets stored in GitHub Actions for identity verification. GitHub's [OpenID Connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect) implementation may  provide a method for identity verification without requiring the storage of long-lived secrets.
