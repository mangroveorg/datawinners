require 'rubygems'
require 'bluepill'
require 'logger'

Bluepill.application(:vpnc) do |app|
  app.process("vpnc") do |process|
    process.pid_file = "/var/run/vpnc/pid"
    process.start_command = "/etc/init.d/vpnc start"
    process.stop_command = "/etc/init.d/vpnc stop"
    process.restart_command = "/etc/init.d/vpnc restart"
    process.start_grace_time = 5.seconds
    process.stop_grace_time = 5.seconds
    process.restart_grace_time = 10 .seconds
    
    process.checks :every => 5.seconds
  end
end