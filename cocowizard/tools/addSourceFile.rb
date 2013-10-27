#!/usr/bin/ruby

require 'rubygems'
require 'json'
require '../../../../../vendors/pbxplorer/lib/pbxplorer'

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

    addToBuild = false

    if fileName =~ /.cpp$/  then fileType = "sourcecode.cpp.cpp"    ; addToBuild = true ; end
    if fileName =~ /.h$/    then fileType = "sourcecode.cpp.h"      ; end
    if fileName =~ /.mm$/   then fileType = "sourcecode.cpp.objcpp" ; addToBuild = true ; end
    if fileName =~ /.c$/    then fileType = "sourcecode.cpp.c"      ; addToBuild = true ; end

    if not fileType then abort("FileType of file not known: " + fileName) end

    file_ref = $project_file.new_object PBXFileReference, { "path" => "../" + path, "sourceTree" => type,  "lastKnownFileType" => "sourcecode.cpp.cpp", "name" => fileName }
    $project_file.add_object(file_ref)

    if addToBuild == true
        build_file = $project_file.new_object PBXBuildFile, { "fileRef" => file_ref.uuid }

        build_phases = $project_file.objects_of_class PBXSourcesBuildPhase
        build_phases.each do |phase| 
            phase["files"] << build_file.uuid 
        end
    end

    group["children"] << file_ref.uuid
end

$project_file = XCProjectFile.new arguments.shift
$main_group = $project_file.project.main_group

arguments.each do|path|
    addFile(path)
end

if not STDIN.tty?
    STDIN.read.split("\n").each do |path|
       addFile(path)
    end
end

$project_file.save
