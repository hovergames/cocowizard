#!/usr/bin/env ruby

require 'rubygems'
require 'json'
require File.dirname(__FILE__) + '/../../vendors/pbxplorer/lib/pbxplorer'

arguments = ARGV

if arguments.length < 1
    abort("Usage: #{$0} xcodeProjectFile")
end

if not STDIN.tty?
    STDIN.read.split("\n").each do |path|
       puts(path)
    end
end

abort("IMPLEMENT THIS")
