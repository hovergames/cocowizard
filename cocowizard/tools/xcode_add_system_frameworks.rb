#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require File.dirname(__FILE__) + '/../../vendors/pbxplorer/lib/pbxplorer'
require File.dirname(__FILE__) + '/xcode_add_source.rb'
require File.dirname(__FILE__) + '/xcode_build_settings.rb'

arguments = ARGV

if arguments.length < 1
    abort("Usage: #{$0} xcodeProjectFile library_name required")
end

def add_framework(library_name)
    if get_framework(library_name) then return end
    framework = addFile("Frameworks/" + library_name)
    framework["path"] = "System/Library/Frameworks/" + library_name
    framework["sourceTree"] = "SDKROOT"
    build_settings("remove", "FRAMEWORK_SEARCH_PATHS", "$(SRCROOT)/../Frameworks")
end

def get_framework(library_name)
    $frameworks.each do |framework|
        framework["files"].each do |framework_file|
            build_file = $project_file.object_with_uuid(framework_file)
            file_ref =  $project_file.object_with_uuid(build_file["fileRef"])
            if file_ref["name"] == library_name
                return build_file
            end
        end
    end
    return nil
end

def set_required(library_name, required)
    build_file = get_framework(library_name)
    build_file["settings"] = {} if not build_file.include? "settings"
    build_file["settings"]["ATTRIBUTES"] = [] if not build_file["settings"].include? "ATTRIBUTES"

    attributes = build_file["settings"]["ATTRIBUTES"]
    if required
        attributes << "WEAK"
    else
        attributes.delete("WEAK")
    end
end

$project_file = XCProjectFile.new arguments.shift
$main_group = $project_file.project.main_group
$frameworks = $project_file.objects_of_class PBXFrameworksBuildPhase
$res_buildphase = $project_file.objects_of_class PBXResourcesBuildPhase

if ARGV.length > 1
    libraryName = ARGV[1]
    required = ARGV[2]
    add_framework(library_name)
    setRequired(library_name, required)
end

if not STDIN.tty?
    STDIN.read.split("\n").each do |args|
        parts = args.split(" ")
        library_name = parts[0]
        required = (parts[1] == "0")
        add_framework(library_name)
        set_required(library_name, required)
    end
end

$project_file.save