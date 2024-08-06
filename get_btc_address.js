const bitcoin = require('bitcoinjs-lib');
const bip39 = require('bip39');
const { BIP32Factory } = require('bip32')
const ecc = require('tiny-secp256k1')
const bip32 = BIP32Factory(ecc)
const fs = require('fs');


bitcoin.initEccLib(ecc)

const mnemonic = 'word word word...';
const seed = bip39.mnemonicToSeedSync(mnemonic);

const root = bip32.fromSeed(seed);
const network = bitcoin.networks.bitcoin;


function generateP2SHAddress(index) {
    const path = `m/49'/0'/0'/0/${index}`;
    const child = root.derivePath(path);
    const { address } = bitcoin.payments.p2sh({
        redeem: bitcoin.payments.p2wpkh({ pubkey: child.publicKey, network }),
        network,
    });
    return address;
}

// 生成以3开头的地址
function createKeySpendOutput(publicKey) {
    const myXOnlyPubkey = publicKey.slice(1, 33);
    const commitHash = bitcoin.crypto.taggedHash('TapTweak', myXOnlyPubkey);
    const tweakResult = ecc.xOnlyPointAddTweak(myXOnlyPubkey, commitHash);
    if (tweakResult === null) throw new Error('Invalid Tweak');
    const { xOnlyPubkey: tweaked } = tweakResult;
    return Buffer.concat([
        Buffer.from([0x51, 0x20]),
        tweaked,
    ]);
}

// 生成以bc1p开头的地址
function generateBech32mAddress(index) {
    const path = `m/86'/0'/0'/0/${index}`;
    const child = root.derivePath(path);
    const output = createKeySpendOutput(child.publicKey);
    const address = bitcoin.address.fromOutputScript(output, network);
    return address;
}

let segwitAddresses = [];
let taprootAddresses = [];

for (let i = 0; i < 10000; i++) {
    const p2shAddress = generateP2SHAddress(i);
    const bech32mAddress = generateBech32mAddress(i);
    // console.log(`"${p2shAddress}",`);
    // console.log(`"${bech32mAddress}",`);
    segwitAddresses.push(p2shAddress);
    taprootAddresses.push(bech32mAddress);
}

const addressData = {
    "segwit": segwitAddresses,
    "taproot": taprootAddresses
};

fs.writeFileSync('addresses.json', JSON.stringify(addressData, null, 4));