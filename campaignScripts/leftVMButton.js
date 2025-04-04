<!-- <div class="row">
    <div id="left-vm-node">
        <button id="CallControlsItem-leftVoicemail-button"
            class="btn f9-btn-default f9-tall-btn f9-btn-centered f9-btn-hold f9-btn-red-hover f9-btn-one-across"
            title="End call as Left Voicemail" data-original-title="Left Voicemail">
            <span class="control-label-container">
                <span class="control-label">Left Voicemail</span>
            </span>
        </button>
    </div>
    </div>

    -->



<html>

<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>

<script>
    $(document).ready(function () {

        window.parent.$('span:contains("Interaction")').click();

        window.parent.setInterval(function () {

            if (/Left Voicemail/.test(window.parent.$('#left-vm-node > button > span > span').text()) == false) {

                window.parent.$('#CallControls-audioplayercontainer-node').after(
                    '<div class="row"> <div id="left-vm-node"> <button id="CallControlsItem-leftVoicemail-button" class="btn f9-btn-default f9-tall-btn f9-btn-centered f9-btn-hold f9-btn-red-hover f9-btn-one-across" title="End call as Left Voicemail" data-original-title="Left Voicemail"> <span class="control-label-container"> <span class="control-label">Left Voicemail</span> </span> </button> </div></div>'
                );

                window.parent.$('#left-vm-node', window.parent.document).click(function () {

                    console.info('Left voicemail button clicked');

                    let _five9Metadata; // The Five9 Metadata
                    let _activeCall; // The active call
                    let _cavs;

                    async function getFive9MetaData() {
                        try {
                            console.info("Script: >>> getFive9MetaData");

                            var response = await fetch("https://app.five9.com/appsvcs/rs/svc/auth/metadata", {
                                cache: "no-cache",
                                credentials: "include", // include, same-origin, *omit
                                mode: "cors", // no-cors, cors, *same-origin.
                            })

                            console.info(`Script: getFive9MetaData returned status ${response.status}`);

                            let f9md;
                            if (response.status === 200) {
                                f9md = await response.json();
                            } else {
                                throw `getFive9MetaData returned status ${response.status}`;
                            }
                            _five9Metadata = f9md;

                        } catch (err) {
                            console.error("Script: getFive9MetaData failed: " + err);
                            throw err;
                        }

                    }

                    async function getCallData() {
                        console.info("Script: >>> getCallData");
                        try {

                            let response = await fetch(
                                "https://" +
                                _five9Metadata.metadata.dataCenters[0].apiUrls[0].host +
                                "/appsvcs/rs/svc/agents/" +
                                _five9Metadata.userId +
                                "/interactions/calls",
                                {
                                    method: "GET",
                                    cache: "no-cache",
                                    credentials: "include", // include, same-origin, *omit
                                    mode: "cors", // no-cors, cors, *same-origin.
                                })

                            let calls = await response.json();

                            console.info(`Script: Got Calls`);
                            console.info(calls);

                            _activeCall = null;

                            if (Array.isArray(calls) && calls.length > 0) {
                                _activeCall = calls[0];
                            }

                            if (_activeCall) {
                                console.info(`Script: Found active call`);
                                console.dir(_activeCall);
                            } else {
                                throw "Script: No active call found."
                            }

                        } catch (err) {
                            console.error("Script: getCallData failed: " + err);
                            throw err;
                        }
                    }

                    async function getCAVs() {
                        try {
                            console.info("Script: >>> getCAVs");
                            let response = await fetch(
                                "https://" +
                                _five9Metadata.metadata.dataCenters[0].apiUrls[0].host +
                                "/appsvcs/rs/svc/orgs/" +
                                _five9Metadata.orgId +
                                "/call_variables",
                                {
                                    cache: "no-cache",
                                    credentials: "include", // include, same-origin, *omit
                                    mode: "cors", // no-cors, cors, *same-origin.
                                }
                            )

                            let cavs = await response.json();

                            console.info("Got CAVs");
                            console.dir(cavs);

                            _cavs = cavs;

                        } catch (err) {
                            console.error(err);
                        }
                    }

                    function checkName(cav, name) {
                        if (name) {
                            let parts = name.split(".");
                            if (parts.length >= 2) {
                                if (parts[0] === cav.group && parts[1] === cav.name) {
                                    return true;
                                }
                            }
                        }
                        return false;
                    }

                    function getCAVbyName(name) {
                        if (name) {
                            return _cavs.find((cav) => checkName(cav, name));
                        }
                        return undefined;
                    }

                    async function setCAV(id, value) {
                        try {

                            var cavPayload = {};
                            cavPayload[id] = value;
                            var bodyString = JSON.stringify(cavPayload);

                            console.info("Script: >>> setCav");
                            console.info(bodyString)

                            let response = await fetch(
                                "https://" +
                                _five9Metadata.metadata.dataCenters[0].apiUrls[0].host +
                                "/appsvcs/rs/svc/agents/" +
                                _five9Metadata.userId +
                                "/interactions/calls/" +
                                _activeCall.id +
                                "/variables_2",
                                {
                                    method: "PUT",
                                    cache: "no-cache",
                                    credentials: "include", // include, same-origin, *omit
                                    mode: "cors", // no-cors, cors, *same-origin.
                                    headers: {
                                        "Content-Type": "application/json; charset=utf-8",
                                    },
                                    body: bodyString
                                }
                            )

                            let setCavResp = await response.json();

                            console.info(`Set CAV: ${id} --> ${value}`);
                            console.dir(setCavResp);

                            return setCavResp;


                        } catch (err) {
                            console.error("Script: setCAV failed: " + err);
                        }

                    }

                    async function disposeCall(dispositionId) {
                        console.info("Script: >>> disposeCall");
                        try {

                            let response = await fetch(
                                "https://" +
                                _five9Metadata.metadata.dataCenters[0].apiUrls[0].host +
                                "/appsvcs/rs/svc/agents/" +
                                _five9Metadata.userId +
                                '/interactions/calls/' +
                                _activeCall.id +
                                '/dispose',
                                {
                                    headers: {
                                        "Content-Type": "application/json"
                                    },
                                    method: "PUT",
                                    cache: "no-cache",
                                    credentials: "include", // include, same-origin, *omit
                                    mode: "cors", // no-cors, cors, *same-origin.
                                    body: JSON.stringify({ dispositionId: dispositionId })
                                });

                            await response.json();

                        } catch (err) {
                            console.error("Script: disposeCall failed: " + err);
                            throw err;
                        }
                    }

                    async function leftVMFunc() {
                        try {

                            await getFive9MetaData();
                            getCAVs()
                            await getCallData();

                            if (_activeCall) {

                                let leftVmCav = getCAVbyName("CallSurvey.OB_LeftVM");

                                await setCAV(leftVmCav.id, 'true');

                                disposeCall(1130815);

                            }

                        } catch (ex) {
                            console.error(ex);
                        }
                    }

                    leftVMFunc();

                    return false;
                });
            }
        }, 2000)
    });

</script>


</html>