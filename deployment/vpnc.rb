require 'rubygems'
require 'bluepill'
require 'logger'

module Bluepill
  module ProcessConditions
      class VpnPing < ProcessCondition
          def initialize(options = {})
              @options = options
          end
          def run(pid)
              system("ping -c2 172.25.155.31")
          end
          def check(value)
              value
          end
      end
  end
end

Bluepill.application("vpnc-connect",:log_file => "/var/log/bluepill.log") do |app|
  app.process("vpnc-connect") do |process|
    process.pid_file = "/var/run/vpnc/pid"
    process.start_command = "/etc/init.d/vpnc start"
    process.stop_command = "/etc/init.d/vpnc stop"
    process.restart_command = "/etc/init.d/vpnc restart"
    process.start_grace_time = 45.seconds
    process.stop_grace_time = 15.seconds
    process.restart_grace_time = 45.seconds
    
    process.checks :vpn_ping, :every => 60.seconds, :times => 3

  end
end

