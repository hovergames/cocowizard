#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require File.dirname(__FILE__) + '/xcode_build_settings.rb'
require File.dirname(__FILE__) + '/../../vendors/pbxplorer/lib/pbxplorer'

arguments = ARGV

if arguments.length < 1
    abort("Usage: #{$0} xcodeProjectFile sourceFile [sourceFile2] [sourceFile3] [...]")
end

def getFolder(folderPath)
    parts = folderPath.split("/")
    parentGroup = $main_group
    parts.each do |folder|
        found = false
        if parentGroup == false
            parentGroup = $project_file.objects_of_class(PBXGroup, { "name" => folder}).first
        else
            parentGroup.children.each do |child|
                if folder == child["name"]
                    found = true
                    parentGroup = child
                end
            end
        end
        if found == false
            return false
        end
    end
    return parentGroup
end

def createGroup(folders)
    type = "SOURCE_ROOT"
    group = $main_group
    currentFolderPath = ""

    folders.each do |folder|
        currentFolderPath += folder + "/"

        if getFolder(currentFolderPath) != false
            group = getFolder(currentFolderPath)
        else
            newgroup = $project_file.new_object PBXGroup,{"name" => folder, "children" => [], "sourceTree" => type}
            $project_file.add_object newgroup
            group["children"] << newgroup.uuid
            group = newgroup
        end
        type = "<group>"
    end
    return group
end

def addFile(path)
    puts "Add File: " + path

    fileName = path
    type = "SOURCE_ROOT"
    group = $main_group

    parts = path.split("/")
    if parts.length > 1
        fileName = parts.pop
        group = createGroup(parts)
        type = "<group>"
    end

    child_paths = group.children.map do |child|
        child["path"]
    end

    if child_paths.include?("../" + path)
        return
    end

    add_to_build = false
    link_file = false

    def configure_build_settings(key, path)
        path = File.dirname "$(SRCROOT)/../" + path
        build_settings "add", key, path
    end

    fileType = "sourcecode.cpp.cpp"
    if fileName =~ /.cpp$/       then fileType = "sourcecode.cpp.cpp"    ; add_to_build = true  ; end
    if fileName =~ /.h$/         then fileType = "sourcecode.cpp.h"      ; end
    if fileName =~ /.mm$/        then fileType = "sourcecode.cpp.objcpp" ; add_to_build = true  ; end
    if fileName =~ /.c$/         then fileType = "sourcecode.cpp.c"      ; add_to_build = true  ; end
    if fileName =~ /.bundle$/    then fileType = "wrapper.plug-in"       ; end
    if fileName =~ /.a$/         then fileType = "archive.ar"            ; link_file = true     ; configure_build_settings "LIBRARY_SEARCH_PATHS"  , path; end
    if fileName =~ /.framework$/ then fileType = "wrapper.framework"     ; link_file = true     ; configure_build_settings "FRAMEWORK_SEARCH_PATHS", path; end

    file_ref = $project_file.new_object PBXFileReference, { "path" => "../" + path, "sourceTree" => type,  "lastKnownFileType" => fileType, "name" => fileName }
    $project_file.add_object(file_ref)

    if add_to_build
        build_file = $project_file.new_object PBXBuildFile, { "fileRef" => file_ref.uuid }

        build_phases = $project_file.objects_of_class PBXSourcesBuildPhase
        build_phases.each do |phase|
            phase["files"] << build_file.uuid
        end
    end

    if link_file
        build_file = $project_file.new_object PBXBuildFile, { "fileRef" => file_ref.uuid }

        $frameworks.each do |framework|
            framework["files"] << build_file.uuid
        end
    end

    if fileType == "wrapper.plug-in"
        build_file = $project_file.new_object PBXBuildFile, { "fileRef" => file_ref.uuid }

        $res_buildphase.each do |res|
            res["files"] << build_file.uuid
        end        
    end

    group["children"] << file_ref.uuid

    return file_ref
end

if __FILE__==$0
    $project_file = XCProjectFile.new arguments.shift
    $main_group = $project_file.project.main_group
    $frameworks = $project_file.objects_of_class PBXFrameworksBuildPhase
    $res_buildphase = $project_file.objects_of_class PBXResourcesBuildPhase

    arguments.each do|path|
        addFile(path)
    end

    if not STDIN.tty?
        STDIN.read.split("\n").each do |path|
           addFile(path)
        end
    end

    $project_file.save
end