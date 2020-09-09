# Loops and Conditions


Pattern for handing over dict to included yaml - use variables in template
* main file:
    ```
    - include: 'includeme.yml'
      loop:
        - "{{ftvpn_rz_firewall_host}}"
        - "{{ftvpn_st_firewall_host}}"
      loop_control:
        loop_var: peer_fw_name   # access in included yml like "{{peer_fw}}.ftvpn_cu_peer_address"
    ```
* included yml file (and jinja templates):
    ```
    - set_fact:
       peer_fw: "{{hostvars[peer_fw_name]}}"    #.ftvpn_cu_script_name}}"

    - debug:
        msg: "{{peer_fw.ftvpn_cu_peer_address}}"

    - name: Fix some variables with "ftvpn_type" in name (rename "hq" "rz" "st" to "ft")
      set_fact:
        template_ft2cu_interface_ip: "{{hostvars[inventory_hostname]['ftvpn_' + peer_fw.ftvpn_type + '2cu_interface_ip']}}"

    - debug:
        msg: "{{template_ft2cu_interface_ip}}"
    ```
