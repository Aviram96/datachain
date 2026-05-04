import assert from "node:assert/strict";
import { describe, it } from "node:test";
import hre from "hardhat";

describe("Datachain", async function () {
  const { viem } = await hre.network.create();

  it("deploys", async function () {
    const datachain = await viem.deployContract("Datachain");
    assert.match(datachain.address, /^0x[a-fA-F0-9]{40}$/);
  });
});
