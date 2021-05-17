Download with wildcard

  - name: download latest centos release and gpg
    command: >
      wget --recursive --level=1 --no-parent --no-directories
      --execute robots=off
      --quiet
      --directory-prefix="{{ bootstrap_tmpdir }}/"
      "{{ bootstrap_centos_mirror }}Packages"
      --accept "centos-release-*.rpm,centos-gpg-keys*.rpm,centos-repos*.rpm"
    args:
      warn: false
      creates: "{{ build_dir }}/etc/pki/rpm-gpg"
