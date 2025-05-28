import { useEffect, useState } from "react";
import {
  extend,
  render,
  useExtensionInput,
  BlockStack,
  Button,
  CalloutBanner,
  Heading,
  Image,
  Text,
  TextContainer,
  Separator,
  Tiles,
  TextBlock,
  InlineStack,
  View,
  Layout,
} from "@shopify/post-purchase-ui-extensions-react";

const APP_URL = "https://comic-sega-metabolism-accurately.trycloudflare.com";

extend("Checkout::PostPurchase::ShouldRender", async ({ inputData, storage }) => {
  const postPurchaseOffer = await fetch(`${APP_URL}/api/offer`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${inputData.token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      referenceId: inputData.initialPurchase.referenceId,
    }),
  }).then((response) => response.json());

  await storage.update(postPurchaseOffer);
  return { render: true };
});

render("Checkout::PostPurchase::Render", () => <App />);

export function App() {
  const { storage, inputData, applyChangeset, done } = useExtensionInput();
  const [loading, setLoading] = useState(false);
  const [selectedOfferId] = useState(null);

  const { offers } = storage.initialData;

  const handleImageClick = async (productId) => {
    try {
      await fetch("https://b717-46-99-18-170.ngrok-free.app/click", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: inputData.initialPurchase.buyerId,
          product_id: productId,
          source: "checkout click",
        }),
      });
    } catch (err) {
      console.error("Error calling /click:", err);
    }
  };

  async function handleAcceptOffer(offer) {
    setLoading(true);

    await fetch("https://b717-46-99-18-170.ngrok-free.app/interact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: inputData.initialPurchase.buyerId,
        product_ids: productId,
      }),
    });

    const token = await fetch(`${APP_URL}/api/sign-changeset`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${inputData.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        referenceId: inputData.initialPurchase.referenceId,
        changes: offer.id,
      }),
    }).then((res) => res.json()).then((res) => res.token);

    console.log(token);
    try {
      await applyChangeset(token);
    } catch (err) {
      console.error("applyChangeset failed:", err);
    }
    done();
  }

  return (
    <BlockStack spacing="loose">
      <Layout
        maxInlineSize={0.8}
        media={[
          { viewportSize: "small", sizes: [1] },
          { viewportSize: "medium", sizes: [0.8] },
          { viewportSize: "large", sizes: [0.8] },
        ]}
      >
        <View border="base" padding="base" cornerRadius="large">
          <BlockStack spacing="loose">
            <CalloutBanner title="Recommended for you">
              Based on your purchases we recommend:
            </CalloutBanner>

            <InlineStack wrap spacing="loose">
              {offers.map((offer) => (
                <View key={offer.id} inlineAlignment="start">
                  <BlockStack spacing="tight">
                    <Button
                      padding="none"
                      subdued
                      onPress={() => handleImageClick(offer.product_id)}
                    >
                      <Image
                        description={offer.productTitle}
                        source={offer.productImageURL}
                      />
                    </Button>
                    <Heading>{offer.productTitle}</Heading>
                    <ProductDescription textLines={offer.productDescription} />
                    <TextBlock size="small">€{offer.originalPrice}</TextBlock>
                    <Button
                      onPress={() => handleAcceptOffer(offer)}
                      submit
                      loading={loading && selectedOfferId === offer.id}
                    >
                      Add to cart
                    </Button>
                  </BlockStack>
                </View>
              ))}
            </InlineStack>
          </BlockStack>
        </View>
      </Layout>
    </BlockStack>

  );
}

function ProductDescription({ textLines }) {
  return (
    <BlockStack spacing="xtight">
      {textLines.map((text, index) => (
        <TextBlock key={index} subdued>{text}</TextBlock>
      ))}
    </BlockStack>
  );
}

function MoneyLine({ label, amount }) {
  return (
    <Tiles>
      <TextBlock size="small">{label}</TextBlock>
      <TextContainer alignment="trailing">
        <TextBlock emphasized size="small">{amount ? `$${amount}` : "-"}</TextBlock>
      </TextContainer>
    </Tiles>
  );
}
