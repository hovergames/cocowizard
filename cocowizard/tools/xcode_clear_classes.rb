#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require File.dirname(__FILE__) + '/../../vendors/pbxplorer/lib/pbxplorer'

arguments = ARGV

if arguments.length < 1
    abort("Usage: #{$0} xcodeProjectFile")
end

project_file = XCProjectFile.new arguments.shift
classes = project_file.objects_of_class(PBXGroup, { "name" => "Classes"}).first
build_phases = project_file.objects_of_class PBXBuildPhase
groups = project_file.objects_of_class PBXGroup

classes.children.each do |file_ref|
    build_files = project_file.objects_of_class PBXBuildFile, { "fileRef" => file_ref.uuid }
    build_file_uuids = build_files.map { |obj| obj.uuid }
    build_phases.each { |phase| phase["files"] -= build_file_uuids }
    build_files.each { |obj| project_file.remove_object obj }
    groups.each { |group| group["children"].delete file_ref }
    project_file.remove_object file_ref
end

project_file.save


