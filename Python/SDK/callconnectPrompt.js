define('3rdparty.bundle', [], function () {

    console.log("#### 3rdparty.bundle.js loaded");

    function loadSdkInIframe(url, callback) {
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        document.body.appendChild(iframe);

        iframe.onload = () => {
            console.log("#### Iframe loaded, injecting script: " + url);
            loadScriptInIframe(iframe, url)
                .then(callback)
                .catch(error => console.error("#### Error loading Five9 SDK:", error));
        };

        function loadScriptInIframe(iframe, url) {
            return new Promise((resolve, reject) => {
                console.log("#### Loading SDK Script inside iframe: " + url);
                const script = iframe.contentDocument.createElement('script');
                script.type = 'text/javascript';
                script.src = url;
                script.async = true;

                script.onload = () => resolve(iframe.contentWindow.Five9);
                script.onerror = () => reject(new Error("#### Failed to load script: " + url));

                iframe.contentDocument.head.appendChild(script);
            });
        }

        iframe.src = 'about:blank';
    }

    loadSdkInIframe('https://cdn.prod.us.five9.net/stable/crm-sdk-lib/five9.crm.sdk.js', function (Five9Sdk) {


        if (!Five9Sdk || !Five9Sdk.CrmSdk) {
            console.error("#### SDK load failed or CrmSdk is undefined");
            return;
        }

        const interactionApi = Five9Sdk.CrmSdk.interactionApi();
        const promptNamePlayOnConnect = `Legal_Recording_EN`;

        const allowedCallTypes = [
            "AGENT",
            //"AGENT_PREVIEW",
            //"AUTODIAL",
            //"INBOUND",
            //"OUTBOUND",
            //"OUTBOUND_PREVIEW",
            //"QUEUE_CALLBACK"
        ];

        function playPromptByName(targetPromptName, f9UserId, currentInteractionId) {
            console.log("#### Attempting to play prompt " + targetPromptName);
            interactionApi.executeRestApi({
                path: `/appsvcs/rs/svc/agents/${f9UserId}/prompts`,
                method: 'GET',
                payload: null
            }).then(function (result) {
                let availablePrompts = JSON.parse(result.response);
                availablePrompts.forEach((prompt) => {
                    if (prompt.name === targetPromptName) {
                        console.log("#### Found prompt " + targetPromptName + " with id " + prompt.id);
                        playPromptById(f9UserId, currentInteractionId, prompt.id);
                    }
                });
            }, function (result) {
                console.log("#### FAILED to get prompts:", result);
            });
        }

        function playPromptById(f9UserId, currentInteractionId, promptId) {
            console.log("#### Playing Prompt " + promptId);
            interactionApi.executeRestApi({
                path: `/appsvcs/rs/svc/agents/${f9UserId}/interactions/calls/${currentInteractionId}/audio/player/play_prompt`,
                method: 'PUT',
                payload: JSON.stringify({ "value": promptId })
            }).then(function (result) {
                console.log("#### Prompt Played Result:", result);
            }, function (result) {
                console.log("#### Prompt Played FAILED:", result);
            });
        }

        interactionApi.subscribe({
            callAccepted: (interactionSubscriptionEvent) => {
                console.log("#### Call Accepted", interactionSubscriptionEvent);
                const currentInteractionId = interactionSubscriptionEvent.callData.interactionId;
                const f9UserId = interactionSubscriptionEvent.callData.agentId;
                const callType = interactionSubscriptionEvent.callData.callType;

                console.log("#### Call Type:", callType);
                
                // Uncomment the line below to filter calls by allowed types
                if (!allowedCallTypes.includes(callType)) return;
                
                console.log("#### Subscribing to WebSocket events for call state changes");

                interactionApi.subscribeWsEvent({
                    "4": function (payLoad, context) {
                        console.log("#### WebSocket Event Received", payLoad);
                        
                        // Log the payload structure to ensure we are accessing the correct fields
                        console.log("#### Full WebSocket Payload:", JSON.stringify(payLoad, null, 2));

                        console.log("#### Stored currentInteractionId:", currentInteractionId);
                        console.log("#### Stored f9UserId:", f9UserId);

                        if (payLoad.state === "TALKING") {
                            console.log("#### Condition met, triggering playPromptByName");
                            playPromptByName(promptNamePlayOnConnect, f9UserId, currentInteractionId);
                        } else {
                            console.log("#### Condition NOT met - Incorrect state");
                        }
                    }
                });
            }
        });
    });
});
