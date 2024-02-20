import subprocess
import datetime
from datadog_checks.base import AgentCheck


class GPGKeyCheck(AgentCheck):
    def check(self, instance):
        # Run gpg command to get the expiry date of the key
        try:
            output = subprocess.check_output(['gpg', '--list-keys', '--with-colons', '--fingerprint'], stderr=subprocess.STDOUT)
            lines = output.decode().split('\n')
            key_expirations = {}
            key_id = None
            key_name = None
            for line in lines:
                if line.startswith('pub:'):
                    key_id = line.split(':')[4]
                elif line.startswith('fpr'):
                    key_name = line.split(':')[9]  # Using the key name instead of fingerprint
                    exp_date_line = lines[lines.index(line) + 1]
                    exp_date = datetime.datetime.strptime(exp_date_line.split(':')[9], "%Y-%m-%d")
                    key_expirations[key_id] = {'key_name': key_name, 'fingerprint': key_name, 'expiry_date': exp_date}
                    
            # Compare expiry date with current date
            current_date = datetime.datetime.now()
            for key_id, info in key_expirations.items():
                expiry_date = info['expiry_date']
                days_until_expiry = (expiry_date - current_date).days
                if 0 < days_until_expiry <= 7:
                    self.gauge('gpg.key.expiry_within_7_days', 1, tags=['key_id:{}'.format(key_id), 'key_name:{}'.format(info['key_name']), 'fingerprint:{}'.format(info['fingerprint']), 'days_until_expiry:{}'.format(days_until_expiry)])
                else:
                    self.gauge('gpg.key.expiry_within_7_days', 0, tags=['key_id:{}'.format(key_id), 'key_name:{}'.format(info['key_name']), 'fingerprint:{}'.format(info['fingerprint']), 'days_until_expiry:{}'.format(days_until_expiry)])
        except subprocess.CalledProcessError as e:
            self.log.error('Error running gpg command: %s', e.output.decode())


if __name__ == '__main__':
    check, instances = GPGKeyCheck.from_yaml('/path/to/your/check/conf.yaml')
    for instance in instances:
        check.check(instance)
        check.gauge('gpg.key.check', 1)
