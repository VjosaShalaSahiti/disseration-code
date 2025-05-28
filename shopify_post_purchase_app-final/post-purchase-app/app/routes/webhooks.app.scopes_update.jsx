import { authenticate } from "../shopify.server";
import db from "../db.server";

export const action = async ({ request }) => {
  const { payload, session, topic, shop } = await authenticate.webhook(request);

  console.log(`Received ${topic} webhook for ${shop}`);
  const current = payload.current;

  if (session) {
    await db.session.update({
      where: {
        id: session.id,
      },
      data: {
        scope: current.toString(),
      },
    });
    try {
      const syncResponse = await fetch("https://2cbf-46-99-61-131.ngrok-free.app/sync", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          shop_domain: shop,
          access_token: session.accessToken,
        }),
      });

      const result = await syncResponse.json();

    } catch (err) {
      console.error("Error calling sync:", err.message);
    }
  }

  return new Response();
};
