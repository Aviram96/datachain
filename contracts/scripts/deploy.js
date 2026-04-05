const hre = require("hardhat");

async function main() {
  console.log("Deploying Datachain contract...");

  const Datachain = await hre.ethers.getContractFactory("Datachain");
  const datachain = await Datachain.deploy();

  await datachain.waitForDeployment();

  const address = await datachain.getAddress();
  console.log(`Datachain deployed successfully to: ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});