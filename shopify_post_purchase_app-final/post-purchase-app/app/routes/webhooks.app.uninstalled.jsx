import { authenticate } from "../shopify.server";
import db from "../db.server";

export const action = async ({ request }) => {
  const { shop, session, topic } = await authenticate.webhook(request);

  console.log(`Received ${topic} webhook for ${shop}`);

  if (session) {
    await db.session.deleteMany({ where: { shop } });
    // Call uninstall endpoint
    try {
      const res = await fetch("https://2cbf-46-99-61-131.ngrok-free.app/uninstall", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          shop_domain: shop,
        }),
      });

    } catch (err) {
      console.error("Error calling uninstall API:", err);
    }
  }

  return new Response();
};
