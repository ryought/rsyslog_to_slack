# rsyslog_to_slack

## Install

/etc/rsyslog.d/

```
sudo systemctl restart rsyslog.service
logger -p user.error test
```

## Ubuntu: apparmor

### Edit

/etc/apparmor.d/usr.sbin.rsyslogd

```
profile rsyslogd /usr/sbin/rsyslogd {
  ...
  /etc/rsyslog.d/slack.py cx,
  ...
  profile /etc/rsyslog.d/slack.py {
    #include <abstractions/base>
    network inet  stream,
  }
  ...
}
```

### Disable

```
apt -y install apparmor-utils
aa-disable usr.sbin.rsyslogd
```
