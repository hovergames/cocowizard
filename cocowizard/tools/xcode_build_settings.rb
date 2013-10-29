#!/usr/bin/env ruby

require 'rubygems'
require File.dirname(__FILE__) + '/../../vendors/pbxplorer/lib/pbxplorer'

def build_settings(mode, key, value)
    $settings = $project_file.objects_of_class XCBuildConfiguration
    $settings.each do |config|
        config["buildSettings"] = {} if not config.include? "buildSettings"
        config["buildSettings"][key] = [] if not config["buildSettings"].include? key

        if mode == "set"
            config["buildSettings"][key] = value
        elsif mode == "add"
            old_value = Array(config["buildSettings"][key])
            config["buildSettings"][key] = old_value
            config["buildSettings"][key] << value if not old_value.include? value
        elsif mode == "remove"
            old_value = Array(config["buildSettings"][key])
            config["buildSettings"][key] = old_value
            config["buildSettings"][key].delete value
        elsif mode == "remove_key"
            config["buildSettings"].delete key
        else
            abort("error: invalid mode given")
        end
    end
end

if __FILE__ == $0
    if ARGV.length < 3
        abort("Usage: #{$0} xcodeProjectFile <mode> <key> <value>")
    end
    mode = ARGV[1].downcase
    key = ARGV[2]
    value = ARGV[3]

    $project_file = XCProjectFile.new ARGV[0]
    build_settings(mode, key, value)
    $project_file.save
end
