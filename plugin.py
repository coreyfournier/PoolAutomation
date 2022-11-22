#https://www.domoticz.com/wiki/Developing_a_Python_plugin
"""
<plugin key="PoolAutomation" name="Pool Automation" author="corey.fournier" version="1.0.0" wikilink="http://www.domoticz.com/" externallink="">
    <description>
        <h2>Kodi Media Player Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Comes with three selectable icon sets: Default, Black and Round</li>
            <li>Display Domoticz notifications on Kodi screen if a Notifier name is specified and events configured for that notifier</li>
            <li>Multiple Shutdown action options</li>
            <li>When network connectivity is lost the Domoticz UI will optionally show the device(s) with a Red banner</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Status - Basic status indicator, On/Off. Also has icon for Kodi Remote popup</li>
            <li>Volume - Icon mutes/unmutes, slider shows/sets volume</li>
            <li>Source - Selector switch for content source: Video, Music, TV Shows, Live TV, Photos, Weather</li>
            <li>Playing - Icon Pauses/Resumes, slider shows/sets percentage through media</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="30px" required="true" default="9090"/>
        <param field="Mode1" label="MAC Address" width="150px" required="false"/>
        <param field="Mode2" label="Shutdown Command" width="100px">
            <options>
                <option label="Hibernate" value="Hibernate"/>
                <option label="Suspend" value="Suspend"/>
                <option label="Shutdown" value="Shutdown"/>
                <option label="Ignore" value="Ignore" default="true" />
            </options>
        </param>
        <param field="Mode3" label="Notifications" width="75px">
            <options>
                <option label="True" value="True"/>
                <option label="False" value="False"  default="true" />
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <description><h2>Debugging</h2>Select the desired level of debug messaging</description>
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""