# rtl_diagram_block
Generate simple rtl diagram block from a json file

## Example

![](example.png)

## Usage

`python gen_diagram_block.py example.json`

## Description

Create your block diagram from a json file.

```java
{ 
	"name": "ip_name",
	"port_list": [
		{
			"name": "clock_name",
			"clock": "True",
			"direction": "input",
			"type": "wire",
			"align": "left"
		},
		{
			"name": "port_name",
			"clock": "false",
			"direction": "output",
			"type": "wire",
			"align": "left"
		},
		{
			"name": "specific_port_name",
			"clock": "false",
			"direction": "interface",
			"type": "interface"
		},
		{
			"name": "specific_port_name",
			"clock": "false",
			"direction": "interface",
			"type": "interface",
			"align": "right"
		}
	]
}
```

