# ansible-add-grafana-annotations

A simple Ansible module to add annotations to Grafana dashboards and panels.

### How to use

- Add the `add_grafana_annotation.py` file in `<ansible-root>/plugins/modules`
- Use it in your playbook/role as following:
```
- name: Create a Grafana annotation
  add_grafana_annotation:
    grafana_api_url: "https://grafana.myproject.com"
    grafana_api_key: "..."
    dashboard_id: 468
    panel_id: 20
    text: "Annotation description"
    tags:
      - tag1
      - tag2
```