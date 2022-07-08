# -*- coding: utf-8 -*-
import ipywidgets as ipw

template = """
<table>
<tr>
  <th style="text-align:center">MarketPlace Use Case 3</th>
<tr>
  <td valign="top"><ul>
    <li><a href="{appbase}/uc3.ipynb" target="_blank">Run application.</a></li>
  </ul></td>
</tr>
</table>
"""


def get_start_widget(appbase, jupbase, notebase):
    html = template.format(appbase=appbase, jupbase=jupbase, notebase=notebase)
    return ipw.HTML(html)
