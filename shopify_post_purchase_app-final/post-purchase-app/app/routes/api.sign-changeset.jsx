import { json } from "@remix-run/node";
import { v4 as uuidv4 } from "uuid";
import jwt from "jsonwebtoken";

import { getSelectedOffer } from "../offer.server";

// Define CORS headers
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

// Handle  CORS request
export const loader = async ({ request }) => {
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders,
    });
  }

  return new Response("OK", {
    status: 200,
    headers: corsHeaders,
  });
};

export const action = async ({ request }) => {
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders,
    });
  }

  const body = await request.json();
  const selectedOffer = await getSelectedOffer(body.changes);
  console.log(body.changes);

  const payload = {
    iss: process.env.SHOPIFY_API_KEY,
    jti: uuidv4(),
    iat: Math.floor(Date.now() / 1000),
    sub: body.referenceId,
    changes: selectedOffer
  };

  const token = jwt.sign(payload, process.env.SHOPIFY_API_SECRET);

  return new Response(JSON.stringify({ token }), {
    status: 200,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json",
    },
  });
};

