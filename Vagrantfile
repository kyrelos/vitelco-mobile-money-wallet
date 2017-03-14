# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  #config.ssh.username = "vagrant"
  #config.ssh.password = "vagrant"

  config.vm.define :app do |app|
    app.vm.network :private_network, ip: "10.0.0.77"
    app.vm.provision :shell, :path => "devops/vagrant_bootstrap.sh"
  end


  # Global configuration

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu/trusty64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  # I got the url from : http://www.vagrantbox.es/
  config.vm.box_url = "ubuntu/trusty64" #"https://oss-binaries.phusionpassenger.com/vagrant/boxes/latest/ubuntu-14.04-amd64-vbox.box"

  # Cache apt packages between Vagrant runs
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

  # Enable agent forwarding
  config.ssh.forward_agent = true

  # Share devops folder with guest VM. VirtualBox mounts shares with
  # all files as executable by default, which causes Ansible to try
  # and execute inventory files (even when they are not scripts.) The
  # mount options below prevent this.
  config.vm.synced_folder './devops', '/vagrant/devops',
      :mount_options => ['fmode=666']

  # Prevent Ubuntu Precise DNS resolution from mysteriously failing
  # http://askubuntu.com/a/239454
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.memory = 2048
    #vb.gui = true
  end

  # TODO: create an Ansible provisioner that targets Linux hosts.

  # Cache apt-get package downloads to speed things up
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
    config.cache.enable :generic, { :cache_dir => "/var/cache/pip" }
  end

end
