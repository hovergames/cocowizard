#!/usr/bin/ruby

require "rubygems"
require 'json'
require '../pbxplorer/lib/pbxplorer'

arguments = ARGV

if arguments.length < 2
	abort("Usage: #{$0} xcodeProjectFile sourceFile [sourceFile2] [sourceFile3] [...]")
end

$project_file = XCProjectFile.new arguments[0]
project = $project_file.project
targets = project.targets

arguments.shift

$group_classes = $project_file.objects_of_class(PBXGroup, { "name" => "Classes"}).first

def createGroup(folders)
	type = "SOURCE_ROOT"
	lastGroup = $group_classes
	folders.each do |folder|
		newgroup = $project_file.new_object PBXGroup,{"name" => folder, "children" => [], "sourceTree" => type}
		$project_file.add_object newgroup
		lastGroup["children"] << newgroup.uuid
		lastGroup = newgroup		
		type = "<group>"
	end
	return lastGroup
end

arguments.each do|path|
	parts = path.split("/")
	if parts.length > 1
		fileName = parts.pop
		lastGroup = createGroup(parts)	
		type = "<group>"
	else
		fileName = path
		lastGroup = $group_classes
		type = "SOURCE_ROOT"
	end

	file_ref = $project_file.new_object PBXFileReference, { "path" => "Classes/" + path, "sourceTree" => type,  "lastKnownFileType" => "sourcecode.cpp.cpp", "name" => fileName }
	$project_file.add_object(file_ref)
    lastGroup["children"] << file_ref.uuid
end

$project_file.save