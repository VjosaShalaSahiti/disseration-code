import { json } from "@remix-run/node";
import { userInfo } from "os";
import { getOffers } from "../offer.server";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization", // 
};

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

  const offers = await getOffers(userid);

  return new Response(JSON.stringify({ offers }), {
    status: 200,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json",
    },
  });
};
